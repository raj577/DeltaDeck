import React, { useState, useRef, useEffect } from 'react'

// Helper component for the loading spinner
const LoadingSpinner = () => (
    <div className="flex items-center justify-center space-x-2">
        <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse [animation-delay:-0.3s]"></div>
        <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse [animation-delay:-0.15s]"></div>
        <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></div>
    </div>
)

// Helper component for the AI's response
const AiResponse = ({ text }) => {
    // Format the text with line breaks and basic markdown-like formatting
    const formattedText = text.split('\n').map((line, index) => {
        // Handle bold text (simple **text** format)
        const boldFormatted = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')

        return (
            <div key={index} className="mb-2">
                <span dangerouslySetInnerHTML={{ __html: boldFormatted }} />
            </div>
        )
    })

    return (
        <div className="mt-6 p-6 bg-gradient-to-br from-gray-50 to-gray-100 border border-gray-200 rounded-xl shadow-inner">
            <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-white text-sm font-bold">AI</span>
                </div>
                <div className="flex-1">
                    <div className="text-gray-800 text-sm leading-relaxed font-medium">
                        {formattedText}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default function GeminiChat({ resetWelcome = false }) {
    // State management for the chat
    const [question, setQuestion] = useState('')
    const [answer, setAnswer] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState('')
    const [showWelcome, setShowWelcome] = useState(true)
    
    // Ref for auto-scrolling to answer
    const answerRef = useRef(null)

    // Reset welcome message when resetWelcome prop changes
    useEffect(() => {
        if (resetWelcome) {
            console.log('🔄 Resetting welcome message for mobile modal')
            setShowWelcome(true)
            setQuestion('')
            setAnswer('')
            setError('')
        }
    }, [resetWelcome])

    // Debug logging for welcome state
    useEffect(() => {
        console.log('🤖 GeminiChat state:', { showWelcome, answer, error, isLoading, resetWelcome })
    }, [showWelcome, answer, error, isLoading, resetWelcome])

    // Auto-scroll to answer when it appears
    useEffect(() => {
        if (answer && answerRef.current) {
            // Small delay to ensure the content is rendered
            setTimeout(() => {
                answerRef.current.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start',
                    inline: 'nearest'
                })
            }, 100)
        }
    }, [answer])

    // Hide welcome message when user starts interacting
    const handleQuestionChange = (e) => {
        setQuestion(e.target.value)
        if (showWelcome && e.target.value.trim()) {
            setShowWelcome(false)
        }
    }

    const handleQuickQuestion = (quickQuestion) => {
        setQuestion(quickQuestion)
        setShowWelcome(false)
    }

    /**
     * Handles the submission of a question to the Gemini API.
     */
    const handleAskGemini = async () => {
        if (!question.trim()) {
            setError('Please enter a question.')
            return
        }

        setIsLoading(true)
        setAnswer('')
        setError('')

        // The prompt is engineered to restrict the AI's responses to option spreads
        const engineeredPrompt = `You are an expert AI assistant that specializes ONLY in financial option spreads (e.g., bull call spread, bear put spread, iron condor, butterfly spread, calendar spread, etc.). Your sole purpose is to answer questions clearly and concisely about these topics.

If the user asks a question about anything other than option spreads (such as specific stocks, cryptocurrencies, general news, coding, or any other unrelated topic), you MUST refuse to answer.

Your ONLY response in that case must be this exact phrase: "I can only answer questions related to option spreads."

Do not provide any other information or pleasantries if the question is off-topic.

For valid option spread questions, provide clear, educational answers that help traders understand the strategy, its risks, rewards, and when to use it.

User's question: "${question}"`

        try {
            // Call our backend API instead of Google directly (solves CORS issue)
            console.log('🚀 Calling Render API:', 'https://option-spreads-api.onrender.com/api/gemini-chat')
            const response = await fetch('https://option-spreads-api.onrender.com/api/gemini-chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: engineeredPrompt })
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || `API request failed with status ${response.status}`)
            }

            const result = await response.json()
            setAnswer(result.answer)

        } catch (err) {
            console.error("Error calling Gemini API:", err)
            setError(`Sorry, something went wrong: ${err.message}`)
        } finally {
            setIsLoading(false)
        }
    }

    /**
     * Handles the key press event for the input field.
     */
    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !isLoading) {
            handleAskGemini()
        }
    }

    return (
        <div className="h-full">
            {/* Header Section */}
            <div className="mb-6">
                <div className="flex items-center space-x-3 mb-2">
                    <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg">
                        <span className="text-white font-bold">🤖</span>
                    </div>
                    <div>
                        <h2 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                            DeltaDeck AI
                        </h2>
                        <p className="text-sm text-gray-600 font-medium">Ask questions about option spread strategies</p>
                    </div>
                </div>
            </div>

            {/* Input Section */}
            <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-xl border border-gray-200 shadow-inner mb-6">
                <label htmlFor="question-input" className="block text-sm font-semibold text-gray-700 mb-3">
                    Ask about option spreads:
                </label>

                <div className="space-y-3">
                    <input
                        id="question-input"
                        type="text"
                        value={question}
                        onChange={handleQuestionChange}
                        onKeyPress={handleKeyPress}
                        placeholder="e.g., What is a bull call spread?"
                        className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all shadow-sm text-gray-900 placeholder-gray-500"
                        disabled={isLoading}
                    />

                    <button
                        onClick={handleAskGemini}
                        disabled={isLoading || !question.trim()}
                        className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-gray-400 disabled:to-gray-500 rounded-lg font-semibold text-white transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none disabled:cursor-not-allowed flex items-center justify-center"
                    >
                        {isLoading ? (
                            <>
                                <LoadingSpinner />
                                <span className="ml-3">Thinking...</span>
                            </>
                        ) : (
                            <>
                                <span className="mr-2">✨</span>
                                Ask DeltaDeck AI
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Quick Questions */}
            <div className="mb-6">
                <p className="text-sm font-medium text-gray-600 mb-3">Quick questions:</p>
                <div className="flex flex-wrap gap-2">
                    {[
                        "What is a bull call spread?",
                        "How does an iron condor work?",
                        "When to use butterfly spreads?",
                        "Bear put spread example"
                    ].map((quickQuestion, index) => (
                        <button
                            key={index}
                            onClick={() => handleQuickQuestion(quickQuestion)}
                            className="px-3 py-2 bg-white hover:bg-gray-50 border border-gray-200 hover:border-purple-300 rounded-lg text-xs font-medium text-gray-700 hover:text-purple-700 transition-all duration-200 shadow-sm hover:shadow-md"
                        >
                            {quickQuestion}
                        </button>
                    ))}
                </div>
            </div>

            {/* Response Section */}
            <div className="min-h-[200px]">
                {error && (
                    <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                        <div className="flex items-start space-x-3">
                            <span className="text-red-500 text-lg">⚠️</span>
                            <p className="text-red-700 text-sm font-medium">{error}</p>
                        </div>
                    </div>
                )}

                {answer && <div ref={answerRef}><AiResponse text={answer} /></div>}

                {!answer && !error && !isLoading && showWelcome && (
                    <div className="p-6 bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-xl shadow-inner animate-pulse">
                        <div className="flex items-start space-x-3">
                            <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0">
                                <span className="text-white text-sm font-bold">AI</span>
                            </div>
                            <div className="flex-1">
                                <div className="text-gray-800 text-sm leading-relaxed font-medium">
                                    <div className="mb-4 text-center">
                                        <div className="text-2xl mb-2">🤖</div>
                                        <div className="text-lg font-bold text-purple-700 mb-2">
                                            Ask DeltaDeck AI!
                                        </div>
                                        <div className="text-sm text-gray-600">
                                            I'm your option spreads expert. Ask me anything about:
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 gap-2 mb-4">
                                        <div className="text-xs bg-white/70 rounded-lg p-2 text-center">
                                            📈 Bull Call Spreads
                                        </div>
                                        <div className="text-xs bg-white/70 rounded-lg p-2 text-center">
                                            📉 Bear Put Spreads
                                        </div>
                                        <div className="text-xs bg-white/70 rounded-lg p-2 text-center">
                                            🦋 Iron Butterflies
                                        </div>
                                        <div className="text-xs bg-white/70 rounded-lg p-2 text-center">
                                            🔄 Iron Condors
                                        </div>
                                    </div>
                                    <div className="text-center">
                                        <div className="text-purple-700 font-bold text-sm animate-bounce">
                                            👆 Type your question above or click quick questions!
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {!answer && !error && !isLoading && !showWelcome && (
                    <div className="text-center py-12 text-gray-500">
                        <div className="text-4xl mb-4">💭</div>
                        <p className="text-sm font-medium">Ask me anything about option spreads!</p>
                        <p className="text-xs mt-2">I specialize in bull/bear spreads, iron condors, butterflies, and more.</p>
                    </div>
                )}
            </div>
        </div>
    )
}